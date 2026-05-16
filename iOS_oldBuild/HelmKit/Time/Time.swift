//
//  Time.swift
//  HelmKit
//
//  Created by Jordan Trana on 7/13/18.
//  Copyright © 2018 Jordan Trana. All rights reserved.
//

import Foundation

extension Date {
    
    init?(year: Int, month: Int, day: Int, timeZone:TimeZone, hour:Int, minute:Int) {
        
        // Specify date components
        var dateComponents = DateComponents()
        dateComponents.year = year
        dateComponents.month = month
        dateComponents.day = day
        dateComponents.timeZone = timeZone
        dateComponents.hour = hour
        dateComponents.minute = minute
        
        // Create date from components
        let userCalendar = Calendar.current // user calendar
        guard let date = userCalendar.date(from: dateComponents) else { return nil }
        self = date
    }
}

extension TimeInterval {
    
    func toYears() -> Double {
        return self / 3.154e+7
    }
    
}
