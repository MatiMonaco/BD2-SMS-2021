# TP FINAL BD2 - Persistencia Poliglota

<br />
<p align="center">
  <a href="https://github.com/MatiMonaco/BD2-SMS-2021">
    <img src="logo.png" alt="Logo" width="234" height="115">
  </a>

<h3 align="center">Red de usuarios Github utilizando MongoDB y Neo4j</h3>

## Tabla de Contenidos

- [TP FINAL BD2 - Persistencia Poliglota](#tp-final-bd2---persistencia-poliglota)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Empezando](#empezando)
    - [Requisitos](#requisitos)
    - [Instalación](#instalación)
      - [Persistencia](#persistencia)
      - [Dependencias](#dependencias)
  - [Modo de uso](#modo-de-uso)
  - [Popular bases de datos](#popular-bases-de-datos)
  - [Funcionalidad](#funcionalidad)
  - [Presentacion](#presentacion)

## Empezando

Instrucciones para correr el programa

### Requisitos

1. Tener instalado python3 (3.9.0)
2. Tener instalado pip3
3. Tener instalado docker (opcional)

### Instalación

#### Persistencia

Para la parte de persistencia hay que tener MongoDB y Neo4j instalados. La
manera recomendada es usando docker con los siguentes comandos:

**MongoDB**

1. Descargar la version oficial de MongoDB

```sh
docker pull mongo
```

2. Levantar el contenedor

```sh
docker run --name Mymongo -p 27017:27017 -d mongo
```

**Neo4j**

1. Descargar la version oficial de Neo4j

```sh
docker pull neo4j
```

2. Levantar el contenedor

```sh
docker run --name Myneo4j -p 7474:7474 -p 7687:7687 --env=NEO4J_AUTH=none -d neo4j
```

#### Dependencias

**Python**

Para instalar las dependencias hay que ejecutar el siguiente comando desde la
carpeta raíz del proyecto:

```sh
pip3 install -r requirements.txt
```

**Env**

Hay que crear un archivo 'env' (sin punto previo ni extensión) en la carpeta raíz del proyecto con la siguiente
estructura:

```
SERVER_HOST=127.0.0.1
PORT=8000
MONGO_DETAILS:mongodb://localhost:27017/
NEO4J_DETAILS=neo4j://localhost:7474/
NEO4J_USER:admin
NEO4J_PASS:admin
GITHUB_API_TOKEN=**token propio para acceder al api de github**
```

Esos datos corresponden al proyecto corriendo en una computadora local con los
puertos por defecto como fueron establecidos en la sección de
[persistencia](#persistencia)

El token de github se puede obtener siguiendo las instrucciones del siguiente
[link](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)

## Modo de uso

1. Encender los contenedores de docker si no lo estaban

```sh
docker start Mymongo
docker start Myneo4j
```

2. Desde la caperta raíz del proyecto, levantar el api con el siguiente comando:

```sh
python3 main.py
```

Luego se podrá acceder al api desde el navegador en el url y puerto utilizado
en el archivo 'env', por defecto http://localhost:8000/docs

## Popular bases de datos

Se puede agregar información a las bases de datos de dos maneras.

1. Utilizando el endpoint `/register` del api que recibe el nombre de un
   usuario de github y lo agrega junto con sus repos. Ademas agrega usuarios
   seguidos por este usuario en profundidad hasta una determinada profundidad.

   En otras palabras, se agrega a los usuarios que este sigue, a los usuarios
   que siguen los usuarios que este sigue, y asi sucesivamente hasta una
   determinada profundidad.

2. Utilizando scrapers/script para popular datos.

**TODO EXPLICAR MEJOR ESTO**

## Funcionalidad

La siguiente lista consiste de todos los endpoints del api, lo que hacen y ejemplos de parámetros para cada uno.
