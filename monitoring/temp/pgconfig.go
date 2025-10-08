package postgres

import (
	"log"
	"os"
	"time"
	"github.com/jackc/pgx/v5/pgxpool"
)

func PoolConfig() *pgxpool.Config {
	const DefaultMaxConns = int32(4)
	const DefaultMinConns = int32(0)
	const DefaultMaxConnLifetime = time.Hour
	const DefaultMaxConnLifetimeJitter = time.Minute * 2
	const DefaultMaxConnIdleTime = time.Minute * 30
	const DefaultHealthCheckPeriod = time.Minute
	const DefaultConnectTimeout = time.Second * 5

	DatabaseURI := os.Getenv("DATABASEURI")
	poolConfig, err := pgxpool.ParseConfig(DatabaseURI)
	if err != nil {
		log.Fatal("Error Applying Config")
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
