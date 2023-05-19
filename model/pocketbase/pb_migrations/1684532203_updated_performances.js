migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("de6tdz3cz7rbict")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "yivqgutf",
    "name": "order",
    "type": "number",
    "required": false,
    "unique": false,
    "options": {
      "min": null,
      "max": null
    }
  }))

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "qndtkkuv",
    "name": "stats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("de6tdz3cz7rbict")

  // remove
  collection.schema.removeField("yivqgutf")

  // remove
  collection.schema.removeField("qndtkkuv")

  return dao.saveCollection(collection)
})
