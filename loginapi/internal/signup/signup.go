package signup

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	dbconn "github.com/vchen7629/cyphria/login-api/internal/db_connection"
	"golang.org/x/crypto/bcrypt"
)

type SignUpUserRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func HashPassword(password string) (string, error) {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), 11);
	if err != nil {
		return "", err
	}

	return string(hashedPassword), nil
}

func CreateNewUser(username, password string) (bool, error) {
	var inserted bool
	err := dbconn.DBConn.QueryRow(context.Background(), `
		INSERT INTO useraccount (uuid, username, password, creation)
		VALUES (
			$1,
			$2,
			$3,
			$4
		) 
		ON CONFLICT (username) DO NOTHING
		RETURNING true;
	`, uuid.New(), username, password, time.Now()).Scan(&inserted)

	if err == pgx.ErrNoRows {
		return false, nil
	}

	if err != nil {
		return false, fmt.Errorf("error creating a new user: %w", err)
	}
	
	return true, nil
}

func HttpHandler(w http.ResponseWriter, r *http.Request) {
	var payload SignUpUserRequest
	bodyerr := json.NewDecoder(r.Body).Decode(&payload)
	if bodyerr != nil {
		http.Error(w, "Error parsing json", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	hashed, hasherror := HashPassword(payload.Password)
	if hasherror != nil {
		http.Error(w, fmt.Sprintf("Error hashing password: %v", hasherror), http.StatusInternalServerError)
		return
	}

	created, err := CreateNewUser(payload.Username, hashed)

	if err != nil {
		http.Error(w, fmt.Sprintf("Error creating user: %v", err), http.StatusInternalServerError)
		return
	}

	if !created {
		w.Header().Set("Content-Type","application/json")
		w.WriteHeader(http.StatusConflict)
		json.NewEncoder(w).Encode(map[string]string{
			"message": "username or uuid already exists",
		})
		return
	}

	response := map[string]string{
		"message": "user created Successfully!",
	}

	w.Header().Set("Content-Type","application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}