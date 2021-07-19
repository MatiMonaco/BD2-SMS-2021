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
  - [Introduccion](#introduccion)
    - [Requisitos](#requisitos)
    - [Instalación](#instalación)
      - [Persistencia](#persistencia)
      - [Dependencias](#dependencias)
  - [Modo de uso](#modo-de-uso)
  - [Popular bases de datos](#popular-bases-de-datos)
  - [Funcionalidad](#funcionalidad)
  - [Presentacion](#presentacion)

## Introduccion

Queremos armar una red en la cual tenemos proyectos y usuarios obtenidos a
través de Github, cada usuario va a poder puntuar y comentar sobre proyectos.
Se les va a recomendar proyectos en los que puede participar o que le interese
el contenido según la gente que sigue (que contribuyó a dichos proyectos) y sus
preferencias de idiomas de programación. Los datos los obtenemos a través de la
api de github dónde vamos a buscar los repositorios con la mayor cantidad de
estrellas y sus contribuidores para generar los datos con los que vamos a
llenar las tablas. Los usuarios se autenticarían a traves de su cuenta de
Github de donde obtenemos la informacion que necesitemos de su cuenta. Las
bases de datos que vamos a usar son MongoDB y Neo4j. MongoDB vamos a utilizarlo
para guardar los datos de los repositorios, los usuarios, los comentarios y
puntajes sin ningún tipo de relación. Mientras que Neo4j se ocupará de guardar
exclusivamente las relaciones entre nuestras entidades utilizando unicamente un
id.

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

Hay que crear un archivo '.env' (con punto previo pero sin extensión) en la carpeta raíz del proyecto con la siguiente
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
en el archivo '.env', por defecto http://localhost:8000/docs

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

**User register**

- `POST /register`

  Recibe un usuario de github y lo registra a la aplicación siguiendo el formato mencionado en la sección anterior.

  Necesita un cuerpo con el siguiente formato:

  ```json
  {
    "username": "nombre_del_usuario"
  }
  ```

**Repos**

- `GET /repos`

  Devuelve un arreglo con todos los repos de la aplicación.

- `GET /repos/{username}/{reponame}`

  Devuelve la información de un repo en particular. `username` es el nombre
  del dueño del repo y `reponame` es el nombre del repo.

  Por ejemplo para ver la información de este repo en particular se tendría que
  hacer un `GET` al endpoint `/repos/MatiMonaco/BD2-SMS-2021`

- `GET /repos/{username}/{reponame}/reviews`

  Similar al anterior, pero devuelve todas las reseñas hechas a un repositorio.

**Users**

- `GET /users`

  Devuelve un arreglo con todos los usuarios de la aplicación.

- `GET /users/{username}`

  Devuelve la información de un usuario en particular.

- `PUT /users/{username}`

  Permite cambiar la información de un usuario en particular.

  Necesita un cuerpo con el siguiente formato:

  ```json
  {
    "name": "Nombre Apellido",
    "avatar_url": "url a la foto",
    "bio": "Texto descriptivo del usuario",
    "languages": ["Lenguajes", "que", "utiliza", "el", "usuario"],
    "following": 0,
    "followers": 0,
    "html_url": "url al perfil de github del usuario"
  }
  ```

- `GET /users/{username}/following`

  Devuelve un arreglo de usuarios seguidos por el usuario que recibe por url.

- `GET /users/{username}/followed_by`

  Devuelve un arreglo de usuarios que siguen al usuario que recibe por url.

- `POST /users/{username}/follow/{other_username}`

  Hace que el usuario `username` siga al usuario `other_username`.

- `POST /users/{username}/unfollow/{other_username}`

  Hace que el usuario `username` deje de seguir al usuario `other_username`.

- `GET /users/{username}/reviews`

  Devuelve un arreglo de todas las reseñas hechas por el usuario.

- `GET /users/{username}/recommended/repos`

  Devuelve un arreglo de repositorios recomendados para el usuario `username` ordenados por nuestro algoritmo de recomendación.

- `GET /users/{username}/recommended/users`

  Devuelve un arreglo de usuarios recomendados para el usuario `username` ordenados por nuestro algoritmo de recomendación.

**Reviews**

- `POST /reviews`

  Crea una reseña a una repo.

  Necesita un cuerpo con el siguiente formato:

  ```json
  {
    "reviewer": "username de la persona haciendo la reseña",
    "repo_name": "nombre completo del repositorio (ej: MatiMonaco/BD2-SMS-2021)",
    "score": 5,
    "comment": "comentario acerca del repositorio"
  }
  ```

  con el valor `score` siendo un numero con decimales entre 0 y 5.

- `PUT /reviews/{review_id}`

  Permite cambiar la información de una reseña en particular.

  Necesita un cuerpo con el siguiente formato:

  ```json
  {
    "score": 5,
    "comment": "un comentario"
  }
  ```

  Ambos parámetros son opcionales, dejando el valor anterior en su ausencia.

- `DELETE /reviews/{review_id}`

  Borra una reseña.

## Presentacion

[Link a la presentacion](https://docs.google.com/presentation/d/134trzpC-L5x3JhsrilmSkhCyVLgIgSQ3v2Bx9AAffJo/edit#slide=id.ge0dd50c000_0_65)
