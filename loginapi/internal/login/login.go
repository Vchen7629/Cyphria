package login

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	dbconn "github.com/vchen7629/cyphria/login-api/internal/db_connection"
	"golang.org/x/crypto/bcrypt"
)

type LoginCredentials struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type LoginResponse struct {
	Token string `json:"token"`
	Message string `json:"message"`
}

type Claims struct {

}

func AuthenticateUser(username, password string) (bool, error) {
	var storedpasswordhash string;

	err := dbconn.DBConn.QueryRow(context.Background(), 
		"SELECT password FROM useraccount WHERE username = $1",
	username).Scan(&storedpasswordhash)

	if err != nil {
		return false, fmt.Errorf("error querying database: %w", err)
	}

	err = bcrypt.CompareHashAndPassword([]byte(storedpasswordhash), []byte(password))
	if err != nil {
		return false, nil
	}

	return true, nil
}


func LoginHandler(w http.ResponseWriter, r *http.Request) {
	var payload LoginCredentials

	requestbodyerr := json.NewDecoder(r.Body).Decode(&payload)
	if requestbodyerr != nil {
		http.Error(w, "error parsing json body", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	login, err := AuthenticateUser(payload.Username, payload.Password)
	if err != nil {
		log.Printf("Authentication error: %v", err)
		http.Error(w, "Something went wrong", http.StatusInternalServerError)
		return
	}

	if !login {
		w.Header().Set("Content-Type","application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "username or password doesn't match",
		})
	}

	response := map[string]string{
		"message": "Login Successful!",
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(response)
}