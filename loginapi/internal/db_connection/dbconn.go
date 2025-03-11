package dbconn

import (
	"context"
	"fmt"
	"log"
	"time"
	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/vchen7629/cyphria/login-api/config/poolconfig"
)

var DBConn *pgxpool.Pool

func ConnectDatabase() error {
	dbconn, err := pgxpool.NewWithConfig(context.Background(), config.PoolConfig())
	if err != nil {
		return fmt.Errorf("error connecting to the database: %w", err)
	}

	err = dbconn.Ping(context.Background())
	if err != nil {
		dbconn.Close()
		return fmt.Errorf("unable to ping db: %w", err)
	}

	connection, err := dbconn.Acquire(context.Background())
	if err != nil {
		log.Fatal("Error Aquiring the connection from database")
	}

	defer connection.Release()

	fmt.Printf("Successfully Connected to Database\n")
	DBConn = dbconn
	return nil
}

func initializeAccountsTable() error {
	_, err := DBConn.Exec(context.Background(), `
		CREATE TABLE IF NOT EXISTS useraccount (
			uuid UUID UNIQUE PRIMARY KEY,
			username VARCHAR(100) UNIQUE, 
			password VARCHAR(100),
			creation TIMESTAMP
		)
	`)
	if err != nil {
		return fmt.Errorf("error creating useraccount table: %v", err)
	}

	return nil
}

func Main() {
	start := time.Now()
	err := ConnectDatabase()
	if err != nil {
		log.Fatalf("Error Calling Connect Database function: %v", err)
	}

	err = initializeAccountsTable()
	if err != nil {
		log.Fatalf("Error initializing accounts table: %v", err)
	}
	end := time.Now()
	duration := end.Sub(start)
	fmt.Println(duration.String())
}