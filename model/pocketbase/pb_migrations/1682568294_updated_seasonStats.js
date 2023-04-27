migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("7uuptqas4r0v9kd")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "ef4n9xxt",
    "name": "type",
    "type": "number",
    "required": false,
    "unique": false,
    "options": {
      "min": null,
      "max": null
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("7uuptqas4r0v9kd")

  // remove
  collection.schema.removeField("ef4n9xxt")

  return dao.saveCollection(collection)
})
