# coma2-backend

This repository will house the backend functionality for a drink mixer developed in my free time.
This software allows the user to define drink recipes, change the current machine setup and status and order the correct drink based on availability.

## Database

This project uses a simple SQLite Database as the data is straightforward.
The following tables are used:

### cocktail

| Column Name | Data Type | Constraints |
|:------------|:----------|:------------|
| id          | INTEGER   | NOT NULL, PK|
| timestamp   | DATETIME  | NOT NULL    |
| name        | VARCHAR   |             |

### ingredient

| Column Name      | Data Type | Constraints    |
|:-----------------|:----------|:---------------|
| id               | INTEGER   | NOT NULL, PK   |
| timestamp        | DATETIME  | NOT NULL       |
| name             | VARCHAR   |                |
| alcohol_percentage| INTEGER  |                |

### slot

| Column Name       | Data Type | Constraints    |
|:------------------|:----------|:---------------|
| id                | INTEGER   | NOT NULL, PK   |
| ingredient_id     | INTEGER   |                |
| amount_percentage | INTEGER   |                |

### cocktail_ingredient

| Column Name   | Data Type | Constraints    |
|:--------------|:----------|:---------------|
| cocktail_id   | INTEGER   | NOT NULL, PK   |
| ingredient_id | INTEGER   | NOT NULL, PK   |
| amount        | INTEGER   |                |

### Relationships

- `cocktail_ingredient` has a foreign key referencing `ingredient(id)`
- `cocktail_ingredient` has a foreign key referencing `cocktail(id)`

## Resources
<https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy>

