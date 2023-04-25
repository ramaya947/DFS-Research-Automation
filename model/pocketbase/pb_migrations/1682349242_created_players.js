migrate((db) => {
  const collection = new Collection({
    "id": "j7b67bzl1w6244z",
    "created": "2023-04-24 15:14:02.225Z",
    "updated": "2023-04-24 15:14:02.225Z",
    "name": "players",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "1u9fsvhy",
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
        "id": "98x9uctz",
        "name": "fid",
        "type": "text",
        "required": false,
        "unique": false,
        "options": {
          "min": null,
          "max": null,
          "pattern": ""
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
  const collection = dao.findCollectionByNameOrId("j7b67bzl1w6244z");

  return dao.deleteCollection(collection);
})
