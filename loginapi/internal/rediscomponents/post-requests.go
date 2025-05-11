package redisComponents

import (
	"fmt"
	"time"
	"context"
)

type UserData struct {
	Username 	string `redis:"username"`
	CreatedAt 	time.Time `redis:"CreatedAt"`
	UUID	 	string `redis:"uuid"`
}

func CreateRedisSessionID(sessionID string, username string, uuid string) error {
	creationTime := time.Now()
	userdata := &UserData{Username: username, CreatedAt: creationTime, UUID: uuid}

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