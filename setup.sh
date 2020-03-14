# from https://gilberttanner.com/blog/deploying-your-streamlit-dashboard-with-heroku

mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"archy.deberker@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml