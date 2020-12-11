job "fibonacci" {

  datacenters = ["dc1"]
  
  type = "batch"

  group "python" {
    count = 1

    task "fibonacci" {
      # The "driver" parameter specifies the task driver that should be used to
      # run the task.
      driver = "raw_exec"

      # The "config" stanza specifies the driver configuration, which is passed
      # directly to the driver to start the task. The details of configurations
      # are specific to each driver, so please see specific driver
      # documentation for more information.

      artifact {
        source      = "git::https://github.com/UnholyDk/data.git"
        destination = "local/repo"
      }

      config {
        command = "python3"
        args = ["local/repo/fibonacci_number.py"]
      }

      resources {
        cpu    = 500 # 500 MHz
        memory = 256 # 256MB
      }
    }
  }
}
