package login

import (
	"fmt"
	"context"
	"encoding/json"
	"crypto/rand"
	"log"
	"net/http"
	"time"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
)

func GenerateSessionToken() (string, error) {
	tokenString := rand.Text()

	if tokenString == "" {
		return "", fmt.Errorf("Error Generating Random Token")
	}

	return tokenString, nil
}

func SaveSessionTokenPostgres(username string, token string) (error) {
	result, err := dbconn.DBConn.Exec(context.Background(), `
		UPDATE useraccount
		SET sessionid = $2
		WHERE username = $1
	`, username, token)

	if err != nil {
		return fmt.Errorf("Error updating sessionID for username")
	}

	if result.RowsAffected() == 0 {
		return fmt.Errorf("No rows were updated")
	}
	
	return nil
}

func SessionHandler(w http.ResponseWriter, username string, uuid string) {
	tokenString, err := GenerateSessionToken()

	if err != nil {
		w.Header().Set("content-type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Error Generating Session Token",
		})
	}

	redisErr := RedisSessionIDHandler(tokenString, username, uuid)

	if redisErr != nil {
		log.Println("hi")
	}

	sessionErr := SaveSessionTokenPostgres(username, tokenString)

	if sessionErr != nil && sessionErr.Error() == "Error updating sessionID for username" {
		w.Header().Set("content-type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": sessionErr.Error(),
		})
	}

	cookie := http.Cookie{
		Name: 		"accessToken",
		Value: 		tokenString,
		Expires: 	time.Now().Add(24 * time.Hour),
		Path: 		"/",
		Secure:     true,
		HttpOnly:   true,
		SameSite:   http.SameSiteLaxMode,
	}

	http.SetCookie(w, &cookie)

}