(ns tictactoe.core
  (:gen-class)
  (:require [clojure.pprint/pprint :as pprint]))

(defn blank-board
  []
  (let [n 3]
    (take n (repeatedly (take n (repeatedly nil))))))

(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  ;; work around dangerous default behaviour in Clojure
  (alter-var-root #'*read-eval* (constantly false))
  (pprint (blank-board)))
