package redisComponents

import (
	"fmt"
	"context"
)

func RemoveSessionTokenRedis(SessionID string) error {
	result := client.Del(context.Background(), SessionID)

	if result.Err() != nil {
		return fmt.Errorf("Error Deleting Key %s", result.Err())
	}

	return nil
}