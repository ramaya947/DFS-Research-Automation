migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("de6tdz3cz7rbict")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "eyvcmgnq",
    "name": "fpts",
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
  const collection = dao.findCollectionByNameOrId("de6tdz3cz7rbict")

  // remove
  collection.schema.removeField("eyvcmgnq")

  return dao.saveCollection(collection)
})
