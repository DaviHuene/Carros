import streamlit as st
import requests
import pandas as pd

# URLs da API
API_BASE = "http://127.0.0.1:8000/Template/api/v1/cars/"
API_LIST = f"{API_BASE}?skip=0&limit=100"

st.title("Cadastro de Carros")

# --------------------
# 📌 Cadastro de Carro
# --------------------
with st.form("form_cadastro_carro"):
    modelo = st.text_input("Modelo")
    nome = st.text_input("Nome")
    cor = st.text_input("Cor")
    marca = st.text_input("Marca")
    versao = st.text_input("Versão")
    ano = st.number_input("Ano", min_value=1900, max_value=3000, step=1)

    submitted = st.form_submit_button("Cadastrar")
    if submitted:
        dados = {
            "modelo": modelo,
            "nome": nome,
            "cor": cor,
            "marca": marca,
            "versao": versao,
            "ano": ano
        }
        try:
            response = requests.post(API_BASE, json=dados)
            if response.status_code in [200, 201]:
                st.success("Carro cadastrado com sucesso!")
                st.json(response.json())
            else:
                st.error(f"Erro ao cadastrar carro: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Erro na requisição: {str(e)}")

# --------------------------
# 📋 Verificar todos os carros
# --------------------------
with st.expander("Verificar Carros Cadastrados"):
    if st.button("Carregar Carros"):
        try:
            response = requests.get(API_LIST)
            if response.status_code == 200:
                carros = response.json()
                if carros:
                    st.table(pd.DataFrame(carros))
                else:
                    st.info("Nenhum carro cadastrado.")
            else:
                st.error(f"Erro ao carregar carros: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Erro na requisição: {str(e)}")

# ----------------------------
# 🔍 Consultar carro por ID
# ----------------------------
with st.expander("Consultar um carro específico"):
    id_consulta = st.number_input("ID do Carro a ser consultado", min_value=1, step=1, key="consulta_id")
    if st.button("Consultar", key="btn_consultar"):
        try:
            response = requests.get(f"{API_BASE}{id_consulta}/")
            if response.status_code == 200:
                dados_carro = response.json()
                st.success("Carro encontrado com sucesso!")
                st.json(dados_carro)
                st.table(pd.DataFrame([dados_carro]))
            else:
                st.error(f"Carro não encontrado. Código: {response.status_code}")
        except Exception as e:
            st.error(f"Erro na requisição: {str(e)}")

# ----------------------------
# ❌ Deletar carro por ID
# ----------------------------
with st.expander("Deletar carro por ID"):
    id_delete = st.number_input("ID do Carro a ser deletado", min_value=1, step=1, key="delete_id")
    if st.button("Deletar"):
        try:
            response = requests.delete(f"{API_BASE}{id_delete}/")
            if response.status_code == 204:
                st.success("Carro deletado com sucesso!")
            else:
                st.error(f"Erro ao deletar carro: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Erro na requisição: {str(e)}")

# ----------------------------
# ✏️ Atualizar carro por ID
# ----------------------------
with st.expander("Atualizar um carro específico"):
    id_update = st.number_input("ID do Carro a ser atualizado", min_value=1, step=1, key="update_id")
    nome = st.text_input("Nome", key="nome_upd")
    modelo = st.text_input("Modelo", key="modelo_upd")
    cor = st.text_input("Cor", key="cor_upd")

    if st.button("Atualizar"):
        dados_update = {
            "nome": nome,
            "modelo": modelo,
            "cor": cor
        }
        try:
            response = requests.put(f"{API_BASE}{id_update}/", json=dados_update)
            if response.status_code == 200:
                dados_carro = response.json()
                st.success("Carro atualizado com sucesso!")
                st.json(dados_carro)
                st.table(pd.DataFrame([dados_carro]))
            else:
                st.error(f"Erro ao atualizar carro: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Erro na requisição: {str(e)}")
