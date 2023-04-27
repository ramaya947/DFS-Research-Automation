migrate((db) => {
  const collection = new Collection({
    "id": "7uuptqas4r0v9kd",
    "created": "2023-04-26 22:45:26.145Z",
    "updated": "2023-04-26 22:45:26.145Z",
    "name": "seasonStats",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "ej9uqapu",
        "name": "pid",
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
        "id": "bo18pfbr",
        "name": "stats",
        "type": "json",
        "required": false,
        "unique": false,
        "options": {}
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
  const collection = dao.findCollectionByNameOrId("7uuptqas4r0v9kd");

  return dao.deleteCollection(collection);
})
