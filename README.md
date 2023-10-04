# coma2-backend

This repository will house the backend functionality for CocktailMachineV2.

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
