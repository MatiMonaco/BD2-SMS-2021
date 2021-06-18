# Programacion Poliglota - Red de usuarios Github utilizando MongoDB y Neo4j

Queremos armar una red en la cual tenemos proyectos y usuarios obtenidos a través de Github, cada usuario va a poder puntuar y comentar sobre proyectos. Se les va a recomendar proyectos en los que puede participar o que le interese el contenido según la gente que sigue (que contribuyó a dichos proyectos) y sus preferencias de idiomas de programación. Los datos los obtenemos a través de la api de github dónde vamos a buscar los repositorios con la mayor cantidad de estrellas y sus contribuidores para generar los datos con los que vamos a llenar las tablas. Los usuarios se autenticarían a traves de su cuenta de Github de donde obtenemos la informacion que necesitemos de su cuenta. Las bases de datos que vamos a usar son MongoDB y Neo4j. MongoDB vamos a utilizarlo para guardar los datos de los repositorios, los usuarios, los comentarios y puntajes sin ningún tipo de relación. Mientras que Neo4j se ocupará de guardar exclusivamente las relaciones entre nuestras entidades utilizando unicamente un id. 

## MongoDB

Guarda los datos de los usuarios
- UserID
- Github user
- Descripción
- Lenguajes preferidos

Guarda los datos de los Repos
- RepoID
- Estrellas
- Cantidad de Forks
- Lenguajes preferidos

Guarda los review
- reviewID
- Puntaje: Double [1 - 5]
- Comentario: String

## Neo4J

### Relaciones
- User-[Follows]->User
- User-[Contributes]->Repo
- User-[Reviews]->Repo

### Objectos/Nodos
- User
  - userId
- Repo
  - repoId
- Review
  - reviewId

## Funcionalidad

1. Recomendarles repos a los usuarios cliente en base a la gente que sigue
  - Las repos se recomiendan ordenadas por una funcion de stars de la repo, idioma de programacion, etc
2. Recomendarles repos a los usuarios cliente en base a los lenguajes que prefiere
3. Recomendarles a los usuarios otros usuarios de github para seguir
  - Usuarios con mas contribuciones que usen el idioma del usuario
4. Usuario puede comentar/puntuar una repo
5. Usuario puede ver los comentarios/puntaje de una repo


Cuando un usuario levanta una repo lo que ve es:
`/repo/#id`
```json
{
  "name": "Nombre de la repo",
  "link": "link a la repo",
  "score": "Resultado de nuestra funcion de cuanto le va a gustar la repo a un usuario",
  "avgUserScore": 3,
  "comments": [{ "score": 4, "comment": "repo copada"}, {"score": 2, "comment": "otro comment"}, ]
}
```
