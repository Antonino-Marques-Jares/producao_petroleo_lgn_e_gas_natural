# Produção mensal de petróleo, lgn e gas_natural no Brasil

![Porto](plataforma_de_petróleo.jpg)

# Instalações Portuárias
O mapa apresenta de forma **agrupada as instalações portuárias por Município** e informando o **Nome da Instalação, Tipo, Município, Estado e Endereço** das instalações no Município.

# Visualize o mapa em:
[Área de Trampo - Portos](https://www.areadetrampo.com.br/producao-mensal-de-petroleo-lgn-e-gas-natural-no-brasil/)

# Autor:

**Antonino Marques Jares**

# Fonte:
[![GOVBR](govbr.webp)](https://dados.gov.br/dados/conjuntos-dados/producao-de-petroleo-e-gas-natural-por-estado-e-localizacao)

# Arquivos csv a serem feitos download:

- Dados - Produção de petróleo (metros cúbicos) 1997-2025
- Dados - Produção de LGN (metros cúbicos) 1997-2025
- Dados - Produção de gás natural (mil metros cúbicos) 1997-2025

# Atualizado em:

06/07/2025

# Passo 1
Fazer Download dos arquivos acima mencionados.

# Passo 2
Execute producao_petroleo_gas_lgn.ipynb.

Inicialmente vamos criar 3 dataframes: df_petroleo, df_gas_natural e df_lgn.

No primeiro gráfico juntaremos df_petroleo e df_lgn que estão na unidade de medida de metros cúbicos.

No segundo gráfico utilizaremos df_gas_natural que está na unidade de medida de 1000 metros cúbicos.

Antes de gerar o gráfico criamos duas bases de dados uma para cada gráfico, onde fazemos o somatório de produção mês de cada produto.

Após a execução de todos os passos você vai gerar 3 htmls o último tem os dois gráficos no mesmo html.



