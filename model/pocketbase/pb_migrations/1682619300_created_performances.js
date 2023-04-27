migrate((db) => {
  const collection = new Collection({
    "id": "de6tdz3cz7rbict",
    "created": "2023-04-27 18:15:00.970Z",
    "updated": "2023-04-27 18:15:00.970Z",
    "name": "performances",
    "type": "base",
    "system": false,
    "schema": [
      {
        "system": false,
        "id": "kxabybgj",
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
        "id": "hjgcey7j",
        "name": "stats",
        "type": "json",
        "required": false,
        "unique": false,
        "options": {}
      },
      {
        "system": false,
        "id": "9zfcwdll",
        "name": "positions",
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
  const collection = dao.findCollectionByNameOrId("de6tdz3cz7rbict");

  return dao.deleteCollection(collection);
})
