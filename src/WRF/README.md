# Requisitos
Distribuição Linux, para usuários Windows é recomendado o uso do [WSL](https://docs.microsoft.com/en-us/windows/wsl/install).

# Instalação do WRF 4.5
O tutorial original de instalação do WRF é disponível neste [*link*](https://pratiman-91.github.io/2020/07/28/Installing-WRF-4.2.1-on-Ubuntu-LTS-20.04.html).

## Instalando os Pré-Requisitos
```shell 
sudo apt install csh gfortran m4 mpich libhdf5-mpich-dev libpng-dev libnetcdff-dev netcdf-bin ncl-ncarg build-essential
```
```shell 
wget https://www.ece.uvic.ca/~frodo/jasper/software/jasper-1.900.29.tar.gz
tar xvf jasper-1.900.29.tar.gz 
cd jasper-1.900.29/
./configure --prefix=/opt/jasper-1.900.29
make
sudo make install
```

## Obtendo o Código Fonte
```shell
wget https://github.com/wrf-model/WRF/releases/download/v4.5.1/v4.5.1.tar.gz
tar xvf v4.5.1.tar.gz
cd WRF-4.5.1/
```
## Preparando a Instalação
```shell
export NETCDF=/usr
export NETCDF_classic=1
./configure
```
Digite a opção **34** e pressione a tecla *enter*.

Abra o arquivo *configure.wrf* e o edite o trecho que define a configuração *LIB_EXTERNAL*:
```shell
nano configure.wrf
```
```shell
 LIB_EXTERNAL    = \
                      -L$(WRF_SRC_ROOT_DIR)/external/io_netcdf -lwrfio_nf -L/usr/lib -lnetcdff -lnetcdf     
```
Para finalizar a edição *ctrl+O* e em seguida *ctrl+X*.

## Compilando o WRF-Solar
Para habilitar as variáveis de irradiância do módulo WRF-solar, é necessário compilar o WRF com as seguintes modificações no arquivo *Registry/Registry.EM_COMMON*:
```shell
# WRF-Solar
state real swddir ij misc 1 - rdh "SWDDIR" "Shortwave surface downward direct irradiance" "W m-2" ""
state real swddir2 ij misc 1 - rdh "SWDDIR2" "Shortwave surface downward direct irradiance from FARMS" "W m-2" ""
state real swddirc ij misc 1 - rdh "SWDDIRC" "Clear-sky Shortwave surface downward direct irradiance" "W m-2" ""
state real swddni ij misc 1 - rdh "SWDDNI" "Shortwave surface downward direct normal irradiance" "W m-2" ""
state real swddni2 ij misc 1 - rdh "SWDDNI2" "Shortwave surface downward direct normal irradiance from FARMS" "W m-2" ""
state real swddnic ij misc 1 - rdh "SWDDNIC" "Clear-sky Shortwave surface downward direct normal irradiance" "W m-2" ""
state real swddnic2 ij misc 1 - rhd "SWDDNIC2" "Clear-sky Shortwave surface downward direct normal irradiance from FARMS" "W/m^2" ""
state real swddif ij misc 1 - rdh "SWDDIF" "Shortwave surface downward diffuse irradiance" "W m-2" ""
state real swddif2 ij misc 1 - rdh "SWDDIF2" "Shortwave surface downward diffuse irradiance from FARMS" "W m-2" ""
```
Observe que a única modificação é a adiçao do **h** em **- rd**. Para iniciar a compilação deve ser executado o comando:

```shell
./compile -j 2 em_real 2>&1 | tee compile.log
```
A saída esperada é similar a esta:
```shell
--->                  Executables successfully built                  <---
 
-rwxrwxr-x 1 wrf wrf 40691640 Jul 30 12:35 main/ndown.exe
-rwxrwxr-x 1 wrf wrf 40572760 Jul 30 12:35 main/real.exe
-rwxrwxr-x 1 wrf wrf 40048888 Jul 30 12:35 main/tc.exe
-rwxrwxr-x 1 wrf wrf 44609360 Jul 30 12:35 main/wrf.exe
 
==========================================================================
```
Se todos os executáveis (*ndown.exe*, *real.exe*, *tc.exe* e *wrf.exe*) foram gerados tem-se uma instalação com sucesso do WRF.
# Instalação do WPS 4.5
```shell
cd ../
wget https://github.com/wrf-model/WPS/archive/v4.5.tar.gz
tar xvf v4.5.tar.gz
cd WPS-4.5/

export WRF_DIR=../WRF-4.5.1/
export JASPERLIB=/opt/jasper-1.900.29/lib/
export JASPERINC=/opt/jasper-1.900.29/include/

./configure
```
Selecione a opção 1 pressione *enter*.

Abra o arquivo *configure.wps* e o trecho que define a configuração *WRF_LIB*:
```shell
nano configure.wps
```
```shell
WRF_LIB         =       -L$(WRF_DIR)/external/io_grib1 -lio_grib1 \
                        -L$(WRF_DIR)/external/io_grib_share -lio_grib_share \
                        -L$(WRF_DIR)/external/io_int -lwrfio_int \
                        -L$(WRF_DIR)/external/io_netcdf -lwrfio_nf \
                        -L$(NETCDF)/lib  -lnetcdf -lnetcdff

```
Para finalizar a edição *ctrl+O* e em seguida *ctrl+X*.

## Compilando o WPS
```shell
./compile 2>&1 | tee compile.log
```
Ao finalizar digite o comando:
```shell
ls -rlt
```
A saída deve ser algo do tipo:
```shell
lrwxrwxrwx 1 wrf wrf    23 Jul 30 12:46 geogrid.exe -> geogrid/src/geogrid.exe
lrwxrwxrwx 1 wrf wrf    21 Jul 30 12:46 ungrib.exe -> ungrib/src/ungrib.exe
lrwxrwxrwx 1 wrf wrf    23 Jul 30 12:46 metgrid.exe -> metgrid/src/metgrid.exe
```
Se todos os executáveis (*geodrid.exe*, *ungrib.exe* e *metgrid.exe*) foram gerados tem-se uma instalação com sucesso do WPS.

# NCAR Command Language (NCL)

O NCAR Command Language (NCL) é uma linguagem de programação e um ambiente de computação desenvolvido pelo National Center for Atmospheric Research (NCAR) para análise e visualização de dados científicos e geoespaciais, incluindo dados atmosféricos, climatológicos e oceânicos. É uma linguagem e um conjunto de ferramentas amplamente usados na comunidade científica para trabalhar com dados relacionados ao clima e à atmosfera.

## Instalação 

O NCL é utilizado por alguns utilitários (*utils*), e a sua instalação é feita pelo [conda](https://docs.conda.io/en/latest/). Conda é um sistema de gerenciamento e pacotes Python que facilita a instalação de softwares pela linha de comando:

```shell
conda install package_name
```

É necessário ter o [miniconda](https://conda.io/miniconda.html) ou [Anaconda](https://www.anaconda.com/) instalado. É recomendado o uso do miniconda por requerer menos espaço de disco. Para manter atualizado o conda utiliza-se o comando:

```shell
conda update -n root --all
```

## Instalando o miniconda

Para uma instalação rápida da última versão do miniconda, os comandos estão listados a seguir:

```shell
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
```

Após a instalação, para inicializar o Miniconda com os seguintes comandos:

```shell
    ~/miniconda3/bin/conda init bash
    ~/miniconda3/bin/conda init zsh
```

Para testar a instalação, digite no terminal:

```shell
conda -V
```

Deverá aparecer a versão, algo como "conda 4.6.2".

## Criando um ambiente conda e instalando o NCL

É recomendado a instalação do NCL dentro de um [ambiente](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) conda, que será chamado *ncl_stable*. Em um terminal *bash* execute os comandos:

```shell
conda create -n ncl_stable -c conda-forge ncl
source activate ncl_stable
```

Sempre que fechar o terminal e abrí-lo novamente, será necessário reativar o ambiente conda como o comando:

```shell
conda activate ncl_stable
```
### Instalando o wrf-python 
O [WRF-python](https://wrf-python.readthedocs.io/en/latest/index.html) é um conjunto de ferramentas de diagnóstico e interpolação dos dados de saída do modelo WRF-ARW. A forma mais fácil de instalar o wrf-python é por meio do Conda após ativas o ambiente conda (*ncl_stable*), utilizando o comando:

```shell
conda install -c conda-forge wrf-python  
```

## Rodando o módulo WPS

Para rodar o WRF Model, antes é necessário realizar o pré-processamento dos dados geográficos (*Static Geographical Data*) e dos dados metereológicos (*Gridded Metereological Data*). O módulo onde é realizado este pré-processamento é denominado *WRF Preprocessing System* (WPS).

![Alt text](https://www2.mmm.ucar.edu/wrf/OnLineTutorial/images/flow.png)

O processamento dos dados geográficos é realizado pelo programa executável *geogrid.exe*. O processamento dos dados metereológicos (condições de contorno e forecast) é realizado pelo programa executável *ungrib.exe*. A interpolação de ambos os processamentos é feita pelo programa executável *metgrid.exe*, sendo a saída deste programa as entradas do módulo WRF (através do programa *real.exe*). 

### Geogrid

A principal função do *Geogrid* é definir o(s) domínio(s) de simulação e interpolar diversos dados. A configuração de domínio é realizada no arquivo [*namelist.wps*](https://www2.mmm.ucar.edu/wrf/users/namelist_best_prac_wps.html). Cada coluna de dados no arquivo namelist.wps representa um domínio. Um domínio pode ser visto como uma região geográfica em uma determinada coordenada (latitude, longitude) com uma determinada extensão em km. Para verificar se o domínio está na região desejada pode-se utilizar a ferramenta NCL plotgrids:

```shell
ncl util/plotgrids.ncl
```
Para executar o *geogrid* basta utilizar o comando (a partir do diretório raiz do WPS):

```shell
./geogrid.exe
```

### Ungrib

O programa *ungrib* tem  função de desempacotar arquivos metereológicos do tipo GRIB (*GRIB1* e *GRIB2*) em arquivos intermediários que o pre-processamento é capaz de manipular. Arquivos GRIB são encontrados em bancos de dados, um exemplo são os arquivos *Global Forecast System* (GFS):

1. Realize o dowload dos arquivos [GFS](https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/) para a data e o período de previsão desejados;

2. Realizar o *link* com tabelas (Vtable), no caso de uso do GFS:

```shell
ln -sf ungrib/Variable_Tables/Vtable.GFS Vtable
``` 

3. Realizar o *link* com os arquivos GRIB (script localizado na raiz do WPS):
```shell
./link_grib.csh path_to_data
```

4. No arquivo *namelist.wps* o campo *&share* deve definir os parâmetros *start_date*, *end_date*, *interval_seconds* e o campo *&ungrib* definir o parâmetro *prefix = FILE*

5. Para rodar o *ungrib* (a saída gerará arquivos intermediários no formato FILE:YYYY-MM-DD_hh)
```shell
./ungrib
```

### Metgrid
O programa *metgrid* tem  função de interpolar os dados metereológicos com o domínio da simulação. Para executá-lo, basta executar o comando:

```shell
./metgrid.exe
```

A saída do programa será um conjunto de arquivos no formato *met_em.d0X.YYYY-MM-DD_hh:00:00.nc* sendo um arquivos por tempo, para cada domínio ("d0X" representa o domínio).

## WRF Model

Para executar uma simulação real utiliza-se o programa *real.exe*, que interpola verticalmente (solo -> atmosfera) os dados dos arquivos *met_em.* para criar as condições de contorno e as condições inicias. O programa *wrf.exe* tem como entrada os arquivos de saída do programa real.exe, sendo este o último programa a ser executado para gerar o modelo de previsão climática.

Para executar o WRF, segue-se os passos:

1. Mover o terminal para o diretório WRFV4.5/test/em_real

2. Realizar o link dos arquivos *met_em.* a este diretório

```shell
ln -sf path_to_met_em_files/met_em.d0* .
```

3. Editar o arquivo [*namelist.input*](http://www2.mmm.ucar.edu/wrf/users/namelist_best_prac_wrf.html) de acordo com o caso de estudo que deve estar de acordo com os dados do arquivo do WPS *namelist.wps*

4. Executar o programa *real.exe*:

```shell
./real.exe
```
Deverão ser criados arquivos de configuração *wrfinput_dxx* e *wrfbdy_dxx*, para cada domínio.
5. Executar o programa *wrf.exe*:

```shell
./wrf.exe
```
Deverão ser criados arquivos de saída *wrfout_dxx_\[initial_date\]* um para cada domínio. Neste arquivo estará os resultados numéricos com as variáveis metereológicas e solarimétricas (WRF-Solar).