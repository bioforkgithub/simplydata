# TEMPORARY diagnostic for PR #79 (removed before merge): which attached package breaks predict(MASS::lda fit)?
try_lda <- function() {
  env <- new.env()
  set.seed(1)
  env$x <- matrix(rnorm(60), 20); env$g <- rep(c("a", "b"), 10)
  env$simplydata_code <- "f <- MASS::lda(x, g); s <- predict(f)$x; dim(s)"
  r <- tryCatch(eval(parse(text = paste0("local({ out <- NULL; ",
    "utils::capture.output(out <- withCallingHandlers({ eval(parse(text = simplydata_code)) }, ",
    "warning = function(w) invokeRestart('muffleWarning'), message = function(m) invokeRestart('muffleMessage'))); ",
    "out })")), envir = env), error = function(e) conditionMessage(e))
  if (is.character(r)) r else "ok"
}
pkgs <- strsplit(Sys.getenv("PKGS"), ",")[[1]]
cat("start:", try_lda(), "\n")
for (p in pkgs) {
  suppressMessages(suppressWarnings(library(p, character.only = TRUE)))
  res <- try_lda()
  if (res != "ok") {
    cat("BROKEN after attaching", p, ":", res, "\n")
    cat("predict found in:", environmentName(environment(get("predict"))), "\n")
    m <- getS3method("predict", "lda"); cat("predict.lda from:", environmentName(environment(m)), "\n")
    print(find("predict"))
    break
  }
}
cat("end:", try_lda(), "\n")
