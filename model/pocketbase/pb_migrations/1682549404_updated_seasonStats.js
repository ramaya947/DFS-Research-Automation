migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("7uuptqas4r0v9kd")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "f07b0ise",
    "name": "season",
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
  collection.schema.removeField("f07b0ise")

  return dao.saveCollection(collection)
})
