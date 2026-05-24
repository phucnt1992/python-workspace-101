// Aspire TypeScript AppHost
// For more information, see: https://aspire.dev

import { createBuilder } from './.modules/aspire.js';

const builder = await createBuilder();

const db = await builder.addPostgres("db")
    .withContainerName("tododb-postgres")
    .withDataVolume({ name: "tododb-postgres-data" })
    .addDatabase("postgres");

const api = await builder.addUvicornApp("api", "./src/api", "api.main:app")
    .withUv()
    .withHttpEndpoint({ env: "PORT" })
    .withEnvironment("APP_DB_URL", await db.getConnectionProperty("Uri"))
    .withEnvironment("OTEL_SERVICE_NAME", "todo-api")
    .waitFor(db);

await builder.build().run();
