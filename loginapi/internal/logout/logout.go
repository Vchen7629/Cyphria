package logout

import (
	"fmt"
	"context"
	"net/http"
	"encoding/json"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
)

type LogoutCredentials struct {
	UUID string `json:"uuid"`
}

func RemoveSessionTokenDB(uuid string) error {
	if uuid == "" {
		return fmt.Errorf("No uuid provided")
	}

	result, updateErr := dbconn.DBConn.Exec(context.Background(), `
		UPDATE useraccount
		SET sessionid = NULL
		WHERE uuid = $1
	`, uuid)

	if updateErr != nil {
		return fmt.Errorf("Internal Error")
	}

	if result.RowsAffected() == 0 {
		return fmt.Errorf("No rows were updated")
	}

	return nil
}

func Logout(w http.ResponseWriter, r *http.Request) {
	var payload LogoutCredentials

	requestbodyerr := json.NewDecoder(r.Body).Decode(&payload)
	w.Header().Set("Content-Type","application/json")

	if requestbodyerr != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "error parsing json body",
		})
	}

	err := RemoveSessionTokenDB(payload.UUID)

	if err != nil && err.Error() == "No uuid provided" {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "no uuid provided in request",
		})
	} else if err != nil && err.Error() == "Internal Error" {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Internal Error",
		})
	} else if err != nil && err.Error() == "No rows were updated" {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "Error removing sessionid for selected user",
		})
	}

	cookie := &http.Cookie{
		Name: 	"accessToken",
		Value: 	"",
		MaxAge: -1,
		Path: 	"/",
	}

	http.SetCookie(w, cookie)

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"message": "Successfully Logged Out!"})
}