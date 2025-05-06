package redisClient

import (
	"os"
	"sync"
	"strconv"
	"github.com/redis/go-redis/v9"
)

var (
    redisClientInstance  *redis.Client
    once           		  sync.Once
)

type RedisEnv struct {
	Addr 		string 
	Password 	string
	DB 			int
}

func GetRedisClient() *redis.Client {
	db, err := strconv.Atoi(os.Getenv("Redis_DB"))

	if err != nil {
		db = 0
	}

	once.Do(func() {
		redisClientInstance = redis.NewClient(&redis.Options{
			Addr:		os.Getenv("Redis_Addr"),
			Password: 	os.Getenv("Redis_Password"),
			DB:			db,
		})
	})
	return redisClientInstance
}