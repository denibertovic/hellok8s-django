{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  # https://devenv.sh/basics/

  # https://devenv.sh/packages/
  packages = [
    pkgs.watchman
    pkgs.kubectl
    pkgs.aws-vault
    pkgs.kubernetes-helm
    pkgs.openssl
    pkgs.pkg-config
    pkgs.libpq
  ];

  # https://devenv.sh/scripts/

  enterShell = ''
    # needed for psycopg2
    export PATH="${pkgs.libpq.pg_config}/bin:$PATH"
    echo "##############################################"
    echo "Welcome to your development shell...";
    echo "##############################################"
  '';

  # https://devenv.sh/tests/
  enterTest = ''
  '';

  # we use .envrc to source that
  dotenv.disableHint = true;

  # https://devenv.sh/services/

  # uncomment this to enable postgres
  services.postgres = {
    enable = true;
    initialScript = "CREATE USER dev WITH SUPERUSER PASSWORD 'devadminpassword';";
    initialDatabases = [{name = "devdb";}];
    listen_addresses = "localhost";
  };

  # Uncomment to enable redis
  services.redis = {
    enable = true;
    extraConfig = ''
      requirepass devredispassword
      appendonly no
      save ""
    '';
  };

  # https://devenv.sh/languages/
  # languages.nix.enable = true;
  languages.python.enable = true;
  languages.python.version = "3.13";
  languages.python.uv.enable = true;
  languages.python.venv.enable = true;
  languages.python.venv.quiet = true;

  # useful for installing AI agents within the dev environment
  # but also for frontend components if necessary
  languages.javascript = {
    enable = true;
    package = pkgs.nodejs_23;
    yarn.enable = true;
    yarn.package = pkgs.yarn-berry;
    yarn.install.enable = true;
  };
  languages.typescript.enable = true;

  processes = {
    web.exec = "./manage.py runserver";
    css.exec = "yarn watch-css";
    celery.exec = "celery -A project worker --loglevel=info";
  };

  git-hooks.hooks.ruff.enable = true;
  git-hooks.hooks.ruff-format.enable = true;
  git-hooks.hooks.prettier.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
