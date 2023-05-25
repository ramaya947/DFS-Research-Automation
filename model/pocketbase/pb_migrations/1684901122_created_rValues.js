migrate((db) => {
  const collection = new Collection({
    "id": "wuxo88adtns44zu",
    "created": "2023-05-24 04:05:22.123Z",
    "updated": "2023-05-24 04:05:22.123Z",
    "name": "rValues",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "gpatgqt9",
        "name": "position",
        "type": "text",
        "required": false,
        "unique": false,
        "options": {
          "min": null,
          "max": null,
          "pattern": ""
        }
      },
      {
        "system": false,
        "id": "3rmwt1zk",
        "name": "stat",
        "type": "text",
        "required": false,
        "unique": false,
        "options": {
          "min": null,
          "max": null,
          "pattern": ""
        }
      },
      {
        "system": false,
        "id": "iw4s2y0m",
        "name": "rValue",
        "type": "number",
        "required": false,
        "unique": false,
        "options": {
          "min": null,
          "max": null
        }
      }
    ],
    "indexes": [],
    "listRule": null,
    "viewRule": null,
    "createRule": null,
    "updateRule": null,
    "deleteRule": null,
    "options": {}
  });

  return Dao(db).saveCollection(collection);
}, (db) => {
  const dao = new Dao(db);
  const collection = dao.findCollectionByNameOrId("wuxo88adtns44zu");

  return dao.deleteCollection(collection);
})
