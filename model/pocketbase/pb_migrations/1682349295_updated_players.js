migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("j7b67bzl1w6244z")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "bp6ihegr",
    "name": "name",
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
  const collection = dao.findCollectionByNameOrId("j7b67bzl1w6244z")

  // remove
  collection.schema.removeField("bp6ihegr")

  return dao.saveCollection(collection)
})
