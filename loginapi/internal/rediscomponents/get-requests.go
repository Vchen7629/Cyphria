package redisComponents

import (
	"log"
	"fmt"
	"time"
	"context"
	"github.com/Vchen7629/Cyphria/loginapi/config/redis"
)

var client, expireTime = redisClient.GetRedisClient(), time.Hour

func FetchSessionDataRedis(SessionID string) (string, error) {
	databaseQuery := time.Now()

	UserData, err := client.HGetAll(context.Background(), SessionID).Result()

	if err != nil {
		return "", fmt.Errorf("Error Fetching User Data")
	}

	expireErr := client.Expire(
		context.Background(), 
		SessionID, 
		expireTime,
	).Err()

	if expireErr != nil {
		return "",fmt.Errorf("Error Updating Expire time")
	}

	username := UserData["username"]

	timeTotal := time.Since(databaseQuery)
	log.Println("You Queried the Redis Database!", timeTotal)

	return username, nil
}

func CheckSessionExistsRedis(SessionID string) (bool, time.Time, error) {
	UserData, err := client.HGetAll(context.Background(), SessionID).Result()

	if err != nil {
		return false, time.Time{}, fmt.Errorf("Error Scanning %s", err.Error())
	}
	
	if len(UserData) == 0 {
		return false, time.Time{}, fmt.Errorf("SessionID doesnt exist")
	}

	createdAtStr := UserData["CreatedAt"]

	createdAt, err := time.Parse(time.RFC3339, createdAtStr)
	if err != nil {
        return false, time.Time{}, fmt.Errorf("invalid CreatedAt format: %w", err)
    }

	return true, createdAt, nil
}

func CheckIfSessionIsOverAbsoluteExpiration(SessionID string, CreatedAt time.Time) (bool, error) {
	currentTime := time.Now()

	if CreatedAt.Add(time.Hour * 12).Before(currentTime) {
		return false, fmt.Errorf("Session Expired Please Login Again")
	} 

	return true, nil
}
