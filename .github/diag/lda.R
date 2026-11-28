# TEMPORARY diagnostic for PR #79 (removed before merge): which attached packages break predict(MASS::lda fit)?
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
one <- Sys.getenv("ONE")
if (nzchar(one)) {
  suppressMessages(suppressWarnings(library(one, character.only = TRUE)))
  cat("ALONE", one, "->", try_lda(), "\n")
  quit(save = "no")
}
pkgs <- strsplit(Sys.getenv("PKGS"), ",")[[1]]
for (p in pkgs) suppressMessages(suppressWarnings(library(p, character.only = TRUE)))
maskers <- sub("^package:", "", setdiff(find("predict"), "package:stats"))
cat("MASKERS of predict:", maskers, "\n")
for (m in maskers) system2(file.path(R.home("bin"), "Rscript"), c(".github/diag/lda.R"), env = paste0("ONE=", m))
