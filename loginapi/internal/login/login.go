package login

/*import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	dbconn "github.com/vchen7629/cyphria/login-api/internal/db_connection"
)

type LoginCredentials struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func Login(username string, password string) (bool, error) {
	var loginsuccess bool
	fmt.Println("Hello From create new User\n")

	err := dbconn.DBConn.QueryRow(context.Background(), `

	`, username, password).Scan(&loginsuccess)

	/*if err != nil {
		
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

	login, err := Login(payload.Username, payload.Password)
	if err != nil {
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
}*/