## Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    CATEGORY ||--o{ PRODUCT : contains
    USER ||--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : includes
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"

    CATEGORY {
        int id PK
        string name
    }

    PRODUCT {
        int id PK
        string name
        float price
        int category_id FK
    }

    USER {
        int id PK
        string username
        string email
    }
