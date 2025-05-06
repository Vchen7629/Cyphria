package components

import (
	"fmt"
	"context"
	dbconn "github.com/Vchen7629/Cyphria/loginapi/config/postgres"
)

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

func RemoveSessionTokenPostgres(uuid string) error {
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