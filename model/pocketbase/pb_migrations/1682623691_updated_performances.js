migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("de6tdz3cz7rbict")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "y0i5tggx",
    "name": "date",
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

  // remove
  collection.schema.removeField("y0i5tggx")

  return dao.saveCollection(collection)
})
