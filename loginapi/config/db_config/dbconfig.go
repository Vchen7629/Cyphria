package dbconfig

import (
	"log"
	"os"
	"time"
	"github.com/jackc/pgx/v5/pgxpool"
)

func Config() *pgxpool.Config {
	const DefaultMaxConns = int32(4)
	const DefaultMinConns = int32(0)
	const DefaultMaxConnLifetime = time.Hour
	const DefaultMaxConnLifetimeJitter = time.Minute * 2
	const DefaultMaxConnIdleTime = time.Minute * 30
	const DefaultHealthCheckPeriod = time.Minute
	const DefaultConnectTimeout = time.Second * 5

	DatabaseURI := os.Getenv("DATABASEURI")
	dbConfig, err := pgxpool.ParseConfig(DatabaseURI)
	if err != nil {
		log.Fatal("Error Applying Config")
	}

	dbConfig.MaxConns = DefaultMaxConns
	dbConfig.MinConns = DefaultMinConns
	dbConfig.MaxConnLifetime = DefaultMaxConnLifetime
	dbConfig.MaxConnLifetimeJitter = DefaultMaxConnLifetimeJitter
	dbConfig.MaxConnIdleTime = DefaultMaxConnIdleTime
	dbConfig.HealthCheckPeriod = DefaultHealthCheckPeriod
	dbConfig.ConnConfig.ConnectTimeout = DefaultConnectTimeout

	return dbConfig
}