mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"astro.chun@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
[theme]\n\
\n\
base = \"light\"\n\
primaryColor = \"#AB0520\"\n\
backgroundColor = \"#FAFAFA\"\n\
secondaryBackgroundColor = \"#F0F0F0\"\n\
textColor = \"#0C234B\"
\n\
" > ~/.streamlit/config.toml
