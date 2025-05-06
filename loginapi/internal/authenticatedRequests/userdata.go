package authenticatedRequests

import (
	"fmt"
	"errors"
	"context"
	"net/http"
	"database/sql"
	"encoding/json"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
)

func CheckSessionInDatabase(SessionID string) (string, string, error) {
	var username string
	var uuid string

	err := dbconn.DBConn.QueryRow(context.Background(), `
		SELECT username, uuid 
		FROM useraccount
		WHERE sessionid = $1
	`, SessionID).Scan(&username, &uuid)

	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return "", "", fmt.Errorf("No matching SessionID found in database")
		} else {
			return "", "", fmt.Errorf("Error Occured %s", err)
		}
	}

	return username, uuid, nil
}

func FetchUserDataHandler(w http.ResponseWriter, r *http.Request) {
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

	username, uuid, sessionErr := CheckSessionInDatabase(cookie.Value)

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
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{
		"username": username,
		"uuid": uuid,
	})
}