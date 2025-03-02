package dbconn

import (
	"context"
	"fmt"
	"log"
	"time"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/vchen7629/cyphria/login-api/config/db_config"
)

func ConnectDatabase() {
	dbconn, err := pgxpool.NewWithConfig(context.Background(), dbconfig.Config())
	if err != nil {
		log.Fatal("Error Connecting to the database")
	}

	defer dbconn.Close()
	err = dbconn.Ping(context.Background())
	if err != nil {
		log.Fatalf("Unable to Ping databaseL %v", err)
	}

	connection, err := dbconn.Acquire(context.Background())
	if err != nil {
		log.Fatal("Error Aquiring the connection from database")
	}
	defer connection.Release()

	fmt.Printf("Successfully Connected to Database\n")

}

func Main() {
	start := time.Now()
	ConnectDatabase()
	end := time.Now()
	duration := end.Sub(start)
	fmt.Println(duration.String())
}