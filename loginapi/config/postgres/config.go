package postgres

import (
	"os"
	"log"
	"fmt"
	"time"
	"github.com/jackc/pgx/v5/pgxpool"
)

func PgConn() string {
	host := os.Getenv("PG_HOST")
	port := os.Getenv("PG_PORT")
	user := os.Getenv("PG_USER")
	password := os.Getenv("PG_PASS")
	dbname := os.Getenv("PG_DB")
	sslmode := "allow"

	if host == "" {
		log.Fatal("No Host provided")
	} else if port == "" {
		log.Fatal("No Port provided")
	} else if user == "" {
		log.Fatal("No user provided")
	} else if password == "" {
		log.Fatal("No password provide")
	} else if dbname == "" {
		log.Fatal("No dbname provided")
	}

	databaseuri := fmt.Sprintf("postgresql://%s:%s@%s:%s/%s?sslmode=%s", user, password, host, port, dbname, sslmode)

	if databaseuri == "" {
		return ""
	}

	return databaseuri
}

func PoolConfig() *pgxpool.Config {
	const DefaultMaxConns = int32(4)
	const DefaultMinConns = int32(0)
	const DefaultMaxConnLifetime = time.Hour
	const DefaultMaxConnLifetimeJitter = time.Minute * 2
	const DefaultMaxConnIdleTime = time.Minute * 30
	const DefaultHealthCheckPeriod = time.Minute
	const DefaultConnectTimeout = time.Second * 5

	DatabaseURI := PgConn()

	if DatabaseURI == "" {
		log.Fatalln("No database uri provided!")
	}

	poolConfig, err := pgxpool.ParseConfig(DatabaseURI)
	if err != nil {
		log.Fatalf("Error Applying Config: %v", err)
	}

	poolConfig.MaxConns = DefaultMaxConns
	poolConfig.MinConns = DefaultMinConns
	poolConfig.MaxConnLifetime = DefaultMaxConnLifetime
	poolConfig.MaxConnLifetimeJitter = DefaultMaxConnLifetimeJitter
	poolConfig.MaxConnIdleTime = DefaultMaxConnIdleTime
	poolConfig.HealthCheckPeriod = DefaultHealthCheckPeriod
	poolConfig.ConnConfig.ConnectTimeout = DefaultConnectTimeout

	return poolConfig
}