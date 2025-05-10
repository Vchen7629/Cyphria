package authenticatedRequests

import (
	"log"
	"fmt"
	"time"
	"errors"
	"context"
	"net/http"
	"database/sql"
	"encoding/json"
	"github.com/Vchen7629/Cyphria/loginapi/config/redis"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
)

var client = redisClient.GetRedisClient()


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

func CheckSessionInRedis(SessionID string) ( bool, error) {
	var cursor uint64

	_, cursor, err := client.Scan(context.Background(), cursor, SessionID, 1).Result()
	if err != nil {
		return false, fmt.Errorf("Error Scanning %s", err)
	}

	return true, nil
}

func CheckSessionInPostgres(SessionID string) (string, error) {
	var username string
	log.Println("You Queried the Database!")

	databaseQuery := time.Now()
	err := dbconn.DBConn.QueryRow(context.Background(), `
		SELECT username
		FROM useraccount
		WHERE sessionid = $1
	`, SessionID).Scan(&username)
	timeTotal := time.Since(databaseQuery)
	log.Println("You Queried the Database!", timeTotal)

	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return "", fmt.Errorf("No matching SessionID found in database")
		} else {
			return "", fmt.Errorf("Error Occured %s", err)
		}
	}

	return username, nil
}

func FetchUserDataHandler(w http.ResponseWriter, r *http.Request) {
	var (
		username 	string
		sessionErr 	error
	)
	cookie, cookieErr := r.Cookie("accessToken")

	if cookieErr != nil {
        http.Error(w, "Unauthorized", http.StatusUnauthorized)
        return
    }

	sessionToken := cookie.Value

	if sessionToken == "" {
		http.Error(w, "No Session Token Found/Returned", http.StatusNotFound)
		return
	}

	found, err := CheckSessionInRedis(cookie.Value)

	if err == nil && found {
		username, sessionErr = FetchSessionDataRedis(cookie.Value)
	} else {
		username, sessionErr = CheckSessionInPostgres(cookie.Value)
	}

	w.Header().Set("Content-Type", "Application/json")

	if sessionErr != nil && sessionErr.Error() == "No matching SessionID found in database" {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "SessionID not found in database",
		})
	} else if sessionErr != nil {
		w.WriteHeader(http.StatusUnprocessableEntity)
		json.NewEncoder(w).Encode(map[string]string{
			"message": sessionErr.Error(),
		})
	} else {
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(map[string]string{
			"username": username,
		})
	}
}