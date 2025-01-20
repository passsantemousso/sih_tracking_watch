db = db.getSiblingDB("health_watch_data_db"); // Nom de la base de données

db.createUser({
    user: "root",
    pwd: "Admin123",
    roles: [
      {
        role: 'readWrite',
        db: 'health_watch_data_db'
      },
    ],
});

db.createCollection("health_data"); // Créer une collection
