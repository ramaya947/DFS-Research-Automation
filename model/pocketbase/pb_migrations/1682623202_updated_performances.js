migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("de6tdz3cz7rbict")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "d5es2fhy",
    "name": "advancedCurrSeasonStats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "dj8uxhtl",
    "name": "battedBallCurrSeasonStats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "xhnbk7xm",
    "name": "standardLastWeekStats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "5cameszt",
    "name": "advancedLastWeekStats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "gakaed4g",
    "name": "battedBallLastWeekStats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "zmrjbbm7",
    "name": "standardTwoWeekStats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "3xad9hw6",
    "name": "advancedTwoWeekStats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "zdax7o9x",
    "name": "battedBallTwoWeekStats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  // update
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "hjgcey7j",
    "name": "standardCurrSeasonStats",
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
  collection.schema.removeField("d5es2fhy")

  // remove
  collection.schema.removeField("dj8uxhtl")

  // remove
  collection.schema.removeField("xhnbk7xm")

  // remove
  collection.schema.removeField("5cameszt")

  // remove
  collection.schema.removeField("gakaed4g")

  // remove
  collection.schema.removeField("zmrjbbm7")

  // remove
  collection.schema.removeField("3xad9hw6")

  // remove
  collection.schema.removeField("zdax7o9x")

  // update
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "hjgcey7j",
    "name": "stats",
    "type": "json",
    "required": false,
    "unique": false,
    "options": {}
  }))

  return dao.saveCollection(collection)
})
