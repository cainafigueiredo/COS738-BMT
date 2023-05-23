# **Introdução**
Este sistema não foi desenvolvido com o objetivo de permitir consultas sobre qualquer base de dados. Dado o escopo da tarefa e da disciplina, este sistema foca especificamente em permitir consultas sobre a base *CysticFibrosis2*. Apesar disso, é possível estender a implementação a fim de lidar com diferentes bases de dados, e.g., modificando os módulos *[queryProcessor](./src/queryProcessor.py)* e *[indexer](./src/indexer.py)*.

Dito isso, as próximas seções discutem como executar o sistema.

# **Instruções**

## **Instalando as Dependências**

Antes de qualquer coisa, instale todas as bibliotecas necessárias para a execução do sistema.

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ (venv) pip install -r requirements.txt
```

Obs: Este projeto foi desenvolvido com o Python 3.8.10.

## **Obtendo o Conjunto de Dados**

Baixe o conjunto de dados do *[CysticFibrosis2](http://www2.dcc.ufmg.br/livros/irbook/cfc.html)* e salve no diretório de sua preferência.

## **Configurando o Sistema**

Há quatro arquivos de configurações que se encontram neste diretório. O primeiro passo para executar o sistema de recuperação de informação é preencher esses arquivos, conforme indicado a seguir. 

- **PC.CFG**: arquivo de configuração do módulo *Query Processor*. Esse arquivo deve conter as seguintes instruções:
    - **LEIA**: caminho para o arquivo contendo as *queries* e os resultados experados. Na implementação atual, deve ser o caminho para o arquivo ```cfquery.xml```, disponibilizado juntamente com a base *CysticFibrosis2*.
    - **CONSULTAS**: caminho para o arquivo com as *queries* pré-processadas. Esse arquivo, é criado após a execução do módulo *Query Processor* e armazenado como um CSV no caminho especificado por este parâmetro.
    - **ESPERADOS**: caminho para o arquivo com os valores esperados para as *queries*. Esse arquivo, é criado após a execução do módulo *Query Processor* e armazenado como um CSV no caminho especificado por este parâmetro.
    - Exemplo: 
        ```bash
        LEIA=/home/CysticFibrosis2/cfquery.xml
        CONSULTAS=/home/data/preprocessedQueries.csv
        ESPERADOS=/home/data/expectedResults.csv
        ```
        
- **GLI.CFG**: arquivo de configuração do módulo *Inverted List Generator*. Esse arquivo deve conter as seguintes instruções:
    - **LEIA**: caminho para um arquivo contendo os documentos sobre os quais as *queries* serão executadas. Na implementação atual, deve ser o caminho para um dos arquivos ```cf__.xml```, disponibilizado juntamente com a base *CysticFibrosis2*. Caso múltiplos arquivos precisem ser carregados, adicione novas linhas com o parâmetro *LEIA* no arquivo de configurações.
    - **ESCREVA**: caminho para a lista invertida. Esse arquivo, é criado após a execução do módulo *Inverted List Generator* e armazenado como um CSV no caminho especificado por este parâmetro.
    - Exemplo: 
        ```bash
        LEIA=/home/CysticFibrosis2/cf74.xml
        LEIA=/home/CysticFibrosis2/cf75.xml
        LEIA=/home/CysticFibrosis2/cf77.xml
        ESCREVA=/home/data/invertedList.csv
        ```

- **INDEX.CFG**: arquivo de configuração do módulo *Indexer*. Esse arquivo deve conter as seguintes instruções:
    - **LEIA**: deve assumir o mesmo valor que o parâmetro *ESCREVA* do arquivo de configuração *GLI.CFG*.
    - **ESCREVA**: caminho para o modelo. Esse arquivo, é criado após a execução do módulo *Indexer* e armazenado como um *dump* Pickle no caminho especificado por este parâmetro.
    - Exemplo: 
        ```bash
        LEIA=/home/data/invertedList.csv
        ESCREVA=/home/data/model.pkl
        ```

- **BUSCA.CFG**: arquivo de configuração do módulo *Searcher*. Esse arquivo deve conter as seguintes instruções:
    - **MODELO**: deve assumir o mesmo valor que o parâmetro *ESCREVA* do arquivo de configuração *INDEX.CFG*.
    - **CONSULTAS**: deve assumir o mesmo valor que o parâmetro *CONSULTAS* do arquivo de configuração *PC.CFG*.
    - **RESULTADOS**: caminho para o arquivo com os resultados das *queries*. Esse arquivo, é criado após a execução do módulo *Searcher* e armazenado como um CSV no caminho especificado por este parâmetro.
    - Exemplo: 
        ```bash
        MODELO=/home/data/model.pkl
        CONSULTAS=/home/data/preprocessedQueries.csv
        RESULTADOS=/home/data/results.csv
        ```

- **AVALIA.CFG**: arquivo de configuração do módulo *Evaluator*. Esse arquivo deve conter as seguintes instruções:
    - **RESULTADOS**: especifica os arquivos de resultados que devem ser utilizados para gerar as medidas de avaliação e diagramas. Se múltiplos arquivos de resultados serão utilizados, então inclua uma linha desta instrução para cada arquivo de resultados.
    - **NOME**: atribui nomes para os arquivos de resultados. Estes nomes serão utilizados para identificar os conjuntos de resultados dentro do módulo *Evaluator*. Deve haver uma instrução *NOME* para cada arquivo de resultados.
    - **ESPERADOS**: caminho para o arquivo com os resultados esperados para as *queries*. 
    - **ESCREVA_DIRETORIO**: diretório onde as medidas de avaliação e os diagramas serão armazenados
    - Exemplo: 
        ```bash
        RESULTADOS=/home/data/resultados1.csv
        NOME=resultadosComStemmer
        RESULTADOS=resultados2.csv
        NOME=resultadosSemStemmer
        ESPERADOS=/home/data/esperados.csv
        ESCREVA_DIRETORIO=/home/data/avaliacao
        ```

## **Executando o Sistema**

O próximo passo é executar o *script* ```main.py```. Você pode executá-lo no modo de consulta ou no modo de avaliação. Para executar o sistema no modo de consulta, rode o comando abaixo:

```bash
$ python3 main.py -m search
```

Para executá-lo no modo de avaliação, rode o seguinte comando:

```bash
$ python3 main.py -m eval
```