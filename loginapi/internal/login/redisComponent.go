package login

import (
	"context"
	"fmt"
	"time"
	"github.com/Vchen7629/Cyphria/loginapi/config/redis"
)

type UserData struct {
	Username string `redis:"username"`
	UUID	 string `redis:"uuid"`
}

var client, expireTime = redisClient.GetRedisClient(), time.Minute * 5

func CreateReverseMapping(sessionID string, uuid string) (string, error) {
	setErr := client.Set(
		context.Background(),
		uuid,
		sessionID,
		expireTime,
	).Err()

	if setErr != nil {
		return "", fmt.Errorf("Error creating Reverse Mapping in Redis")
	}

	return sessionID, nil
}

func UpdateNewSessionID(sessionID string, username string, uuid string) error {
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


func RedisSessionIDHandler(sessionID string, username string, uuid string) error {
	sessionErr := UpdateNewSessionID(sessionID, username, uuid)

	if sessionErr != nil {
		return fmt.Errorf(sessionErr.Error())
	}

	return nil
}