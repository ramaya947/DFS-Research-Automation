migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("de6tdz3cz7rbict")

  // update
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "kxabybgj",
    "name": "fid",
    "type": "text",
    "required": false,
    "unique": false,
    "options": {
      "min": null,
      "max": null,
      "pattern": ""
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("de6tdz3cz7rbict")

  // update
  collection.schema.addField(new SchemaField({
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
  }))

  return dao.saveCollection(collection)
})
