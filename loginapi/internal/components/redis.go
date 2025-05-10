package components

import (
	"log"
	"fmt"
	"time"
	"context"
	"github.com/Vchen7629/Cyphria/loginapi/config/redis"
)

type UserData struct {
	Username string `redis:"username"`
	UUID	 string `redis:"uuid"`
}

var client, expireTime = redisClient.GetRedisClient(), time.Minute * 5


func FetchSessionDataRedis(SessionID string) (string, error) {
	databaseQuery := time.Now()
	expireTime := time.Minute * 5

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
		return "", fmt.Errorf("Error Updating Expire time")
	}

	username := UserData["username"]
	
	timeTotal := time.Since(databaseQuery)
	log.Println("You Queried the Redis Database!", timeTotal)

	return username, nil
}


func UpdateRedisSessionID(sessionID string, username string, uuid string) error {
	userdata := &UserData{Username: username, UUID: uuid}

	setErr := client.HSet(
		context.Background(), 
		sessionID, 
		userdata, 
	).Err()
	
	if setErr != nil {
		return fmt.Errorf("Error creating SessionID in Redis")
	}

	expireErr := client.Expire(
		context.Background(), 
		sessionID, 
		expireTime,
	).Err()

	if expireErr != nil {
		return fmt.Errorf("Error applying SessionID TTL")
	}

	return nil
}

func CheckSessionExistsRedis(SessionID string) (bool, error) {
	var cursor uint64
	_, cursor, err := client.Scan(context.Background(), cursor, SessionID, 1).Result()

	if err != nil {
		return false, fmt.Errorf("Error Scanning %s", err.Error())
	}

	return true, nil
}

func RemoveSessionTokenRedis(SessionID string) error {
	result := client.Del(context.Background(), SessionID)

	if result.Err() != nil {
		return fmt.Errorf("Error Deleting Key %s", result.Err())
	}

	return nil
}