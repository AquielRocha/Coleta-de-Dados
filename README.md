# 📊 Coleta de Dados

Um projeto para coleta de dados utilizando **Streamlit** e **PostgreSQL**, focado em consultas eficientes e otimização de performance.

## 🚀 Funcionalidades

- Conexão segura com **PostgreSQL** utilizando variáveis de ambiente (`.env`).
- Interface interativa com **Streamlit** para visualização de dados.
- Consultas SQL otimizadas e cacheadas para melhor desempenho.
- Modularização do código para facilitar manutenção e escalabilidade.

## 🛠 Tecnologias Utilizadas

- **Python** (3.8+)
- **Streamlit**
- **PostgreSQL**
- **psycopg2** (para comunicação com o banco de dados)
- **python-dotenv** (para gerenciar credenciais de forma segura)

## 👅 Instalação

1. **Clone o repositório:**
   ```sh
   git clone https://github.com/AquielRocha/Coleta-de-Dados.git
   cd Coleta-de-Dados
   ```

2. **Crie e ative um ambiente virtual (opcional, mas recomendado):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. **Instale as dependências:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure o arquivo `.env`** com suas credenciais do banco de dados:
   ```ini
   DB_NAME=db_samge_hmg
   DB_USER=samge_read
   DB_PASSWORD=samge_read
   DB_HOST=162.243.243.165
   DB_PORT=5432
   ```

5. **Execute a aplicação Streamlit:**
   ```sh
   streamlit run app.py
   ```

## 🎯 Uso

1. Acesse a interface via **navegador** após rodar o Streamlit.
2. Realize consultas ao banco de dados de forma interativa.
3. Visualize os resultados processados diretamente na aplicação.

## 🛡️ Boas Práticas

- **Não compartilhe seu `.env`!** Sempre adicione ele ao `.gitignore`:
  ```ini
  .env
  ```
- Utilize consultas **parametrizadas** para evitar SQL Injection.
- Utilize o **cache do Streamlit** (`@st.cache_data`) para otimizar consultas frequentes.

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. **Fork o projeto**.
2. Crie uma **branch** para sua feature (`git checkout -b minha-feature`).
3. **Commit suas mudanças** (`git commit -m 'Adiciona nova funcionalidade'`).
4. **Push na branch** (`git push origin minha-feature`).
5. Abra um **Pull Request**.

## 🐟 Licença

Este projeto é open-source e distribuído sob a licença [MIT](LICENSE).

---

💡 **Dúvidas ou sugestões?** Entre em contato ou abra uma issue no repositório! 🚀

