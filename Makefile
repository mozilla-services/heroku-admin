UPDATE_BEFORE_COMMIT_FILES := 

help:
	@echo "Targets:"
	@echo "    commit   update any files derived from another, prior to committing"
	@echo "    help     show this text"
	@echo "    test     test everything!"
	@echo "    csv      Generate CSV output for today"
	@echo "    email    Generate email output for today"

email:
	./heroku-2fa.py --email > $$(date -u +%Y-%m-%dT%H:%M:%S%Z_heroku_missing_2FA.csv) \
		|| echo "Some users missing 2fa"

csv:
	./heroku-2fa.py --csv > $$(date -u +%Y-%m-%dT%H:%M:%S%Z_heroku_missing_2FA.csv) \
		|| echo "Some users missing 2fa"

test: 
	@echo "No tests yet"
	false

.PHONY:  test
